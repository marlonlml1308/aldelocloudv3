<?php

namespace App\Filament\Resources;

use App\Filament\Resources\TaxesResource\Pages;
use App\Filament\Resources\TaxesResource\RelationManagers;
use App\Models\Taxes;
use Filament\Forms;
use Filament\Forms\Form;
use Filament\Forms\FormsComponent;
use Filament\Resources\Resource;
use Filament\Tables;
use Filament\Tables\Columns\TextColumn;
use Filament\Tables\Table;
use Illuminate\Database\Eloquent\Builder;
use Illuminate\Database\Eloquent\SoftDeletingScope;

class TaxesResource extends Resource
{
    protected static ?string $model = Taxes::class;
    protected static ?string $navigationGroup = 'Configuracion';
    protected static ?string $navigationIcon = 'heroicon-o-receipt-percent';

    public static function form(Form $form): Form
    {
        return $form
            ->schema([
                //
                Forms\Components\TextInput::make('taxname')
                ->required()
                ->maxLength(30),
                Forms\Components\TextInput::make('taxpercent')
                ->required()
                ->numeric()
                ->minValue(1)
                ->maxValue(100),
            ]);
    }

    public static function table(Table $table): Table
    {
        return $table
            ->columns([
                //
                Tables\Columns\TextColumn::make('taxname'),
                Tables\Columns\TextColumn::make('taxpercent'),
            ])
            ->filters([
                //
            ])
            ->actions([
                Tables\Actions\EditAction::make(),
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

    public static function getPages(): array
    {
        return [
            'index' => Pages\ListTaxes::route('/'),
            'create' => Pages\CreateTaxes::route('/create'),
            'edit' => Pages\EditTaxes::route('/{record}/edit'),
        ];
    }
}
