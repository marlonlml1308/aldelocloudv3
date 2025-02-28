<?php

namespace App\Filament\Resources;

use App\Filament\Resources\ErrorsmdbResource\Pages;
use App\Filament\Resources\ErrorsmdbResource\RelationManagers;
use App\Models\Errorsmdb;
use Filament\Forms;
use Filament\Forms\Form;
use Filament\Resources\Resource;
use Filament\Tables;
use Filament\Tables\Table;
use Illuminate\Database\Eloquent\Builder;
use Illuminate\Database\Eloquent\SoftDeletingScope;

class ErrorsmdbResource extends Resource
{
    protected static ?string $model = Errorsmdb::class;

    protected static ?string $navigationIcon = 'heroicon-o-face-frown';
    protected static ?string $navigationGroup = 'Configuracion';

    public static function form(Form $form): Form
    {
        return $form
            ->schema([
                Forms\Components\TextInput::make('branchid')
                    ->required()
                    ->numeric(),
                Forms\Components\TextInput::make('table')
                    ->required()
                    ->maxLength(255),
                Forms\Components\TextInput::make('idtable')
                    ->required()
                    ->maxLength(255),
                Forms\Components\TextInput::make('name')
                    ->required()
                    ->maxLength(255),
            ]);
    }

    public static function table(Table $table): Table
    {
        return $table
            ->columns([
                Tables\Columns\TextColumn::make('branch.branch')->label('Sucursal')
                ->sortable()
                ->disabledClick(),
                Tables\Columns\TextColumn::make('table')
                    ->sortable()
                    ->label('Tabla'),
                Tables\Columns\TextColumn::make('idtable')
                    ->label('ID en Tabla'),
                Tables\Columns\TextColumn::make('name')
                    ->searchable()
                    ->label('Nombre'),
                Tables\Columns\TextColumn::make('created_at')
                    ->dateTime()
                    ->sortable()
                    ->label('Reportado En'),
            ])
            ->filters([
                //
            ])
            ->actions([
                // Tables\Actions\EditAction::make(),
            ])
            ->bulkActions([
                Tables\Actions\BulkActionGroup::make([
                    Tables\Actions\DeleteBulkAction::make(),
                ]),
            ]);
    }

    public static function getRelations(): array
    {
        return [
            //
        ];
    }
    public static function getModelLabel(): string
    {
        return __(key: 'Error');
    }
    public static function getPluralModelLabel(): string
    {
        return __(key: 'Errores');
    }

    public static function getPages(): array
    {
        return [
            'index' => Pages\ListErrorsmdbs::route('/'),
            'create' => Pages\CreateErrorsmdb::route('/create'),
            'edit' => Pages\EditErrorsmdb::route('/{record}/edit'),
        ];
    }
}
