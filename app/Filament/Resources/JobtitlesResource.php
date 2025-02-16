<?php

namespace App\Filament\Resources;

use App\Filament\Resources\JobtitlesResource\Pages;
use App\Filament\Resources\JobtitlesResource\RelationManagers;
use App\Models\Jobtitles;
use Filament\Forms;
use Filament\Forms\Form;
use Filament\Resources\Resource;
use Filament\Tables;
use Filament\Tables\Table;
use Illuminate\Database\Eloquent\Builder;
use Illuminate\Database\Eloquent\SoftDeletingScope;

class JobtitlesResource extends Resource
{
    protected static ?string $model = Jobtitles::class;
    protected static ?string $navigationGroup = 'Empleados';
    protected static ?string $navigationIcon = 'heroicon-o-user-group';

    public static function form(Form $form): Form
    {
        return $form
            ->schema([
                //
                Forms\Components\TextInput::make('jobtitletext')->label('Cargo')
                ->required()
                ->maxLength(14),
                Forms\Components\Toggle::make('jobtitleinactive')->label('Inactivo')
                ->required()
                ->inline(false),
                Forms\Components\Select::make('defaultsecuritylevel')->label('Nivel de Seguridad')
                ->required()
                ->options([
                    '1' => '1',
                    '2' => '2',
                    '3' => '3',
                    '4' => '4',
                    '5' => '5',
                ])
            ]);
    }

    public static function table(Table $table): Table
    {
        return $table
            ->columns([
                //
                Tables\Columns\TextColumn::make('jobtitletext')->label('Cargo'),
                Tables\Columns\TextColumn::make('defaultsecuritylevel')->label('Nivel de Seguridad'),
                Tables\Columns\CheckboxColumn::make('jobtitleinactive')->label('Inactivo')
                ->disabled(),

            ])
            ->filters([
                //
            ])
            ->actions([
                Tables\Actions\EditAction::make(),
            ])
            ->bulkActions([
                // Tables\Actions\BulkActionGroup::make([
                //     Tables\Actions\DeleteBulkAction::make(),
                // ]),
            ]);
    }

    public static function getRelations(): array
    {
        return [
            //
        ];
    }

    public static function getPages(): array
    {
        return [
            'index' => Pages\ListJobtitles::route('/'),
            'create' => Pages\CreateJobtitles::route('/create'),
            'edit' => Pages\EditJobtitles::route('/{record}/edit'),
        ];
    }
    public static function getModelLabel(): string
    {
        return __(key: 'Cargo');
    }
    public static function getPluralModelLabel(): string
    {
        return __(key: 'Cargos');
    }
}
